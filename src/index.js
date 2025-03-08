const express = require('express');
const path = require('path');
const crypt = require("bcrypt");
const multer = require('multer');
const collection = require('./config');
const fs = require('fs');
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}
const csv = require('csv-parser');
const { spawn } = require('child_process');

const app = express();
app.set('view engine', 'ejs');
app.use(express.static("public"));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

const port = 3000;
app.listen(port, () => {
    console.log(`http://localhost:${port}`);
});

// Set up Multer storage
const storage = multer.diskStorage({
    destination: './uploads/',
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB file size limit
    fileFilter: (req, file, cb) => {
        const fileTypes = /jpeg|jpg|png/;
        const extname = fileTypes.test(path.extname(file.originalname).toLowerCase());
        const mimeType = fileTypes.test(file.mimetype);

        if (mimeType && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Only images (JPG, JPEG, PNG) are allowed!'));
        }
    }
});

// Routes
app.get("/", (req, res) => {
    res.render("login");
});

app.get("/signup", (req, res) => {
    res.render("signup");
});

app.post("/signup", async (req, res) => {
    const data = {
        name: req.body.username,
        password: req.body.password
    };

    const existinguser = await collection.findOne({ name: data.name });
    if (existinguser) {
        res.send("User already exists. Please choose a different username.");
    } else {
        const saltrounds = 10;
        const hashedpass = await crypt.hash(data.password, saltrounds);
        data.password = hashedpass;
        const userdata = await collection.insertMany(data);
        console.log(userdata);
        res.render("home");
    }
});

app.post("/login", async (req, res) => {
    try {
        const check = await collection.findOne({ name: req.body.username });
        if (!check) {
            res.send("Username not found");
            return;
        }
        const isPasswordMatch = await crypt.compare(req.body.password, check.password);
        if (isPasswordMatch) {
            res.render("home");
        } else {
            res.send("Wrong password");
        }
    } catch (error) {
        console.error(error);
        res.status(500).send("An error occurred while logging in");
    }
});

// Serve uploaded files
app.use('/uploads', express.static('uploads'));

// **UPLOAD DRESS IMAGE**
app.get("/upload", (req, res) => {
    res.render("upload");
});

/*app.post("/upload", upload.single('dressImage'), (req, res) => {
    if (!req.file) {
        return res.status(400).send("No file uploaded.");
    }
    res.redirect(`/detect?imagePath=uploads/${req.file.filename}`);
});*/
app.post("/upload", upload.single('dressImage'), (req, res) => {
    if (req.fileValidationError) {
        // Handle file validation errors (e.g., invalid file type)
        return res.status(400).send(req.fileValidationError);
    }

    if (!req.file) {
        // Handle case where no file was uploaded
        return res.status(400).send("No file uploaded.");
    }

    // Log the uploaded file details
    console.log("File uploaded successfully:", req.file);

    // If everything is successful, redirect to the detection page
    res.redirect(`/detect?imagePath=uploads/${req.file.filename}`);
});

// Route to render color detection page
app.get('/detect', async (req, res) => {
    const imagePath = req.query.imagePath;
    
    if (!imagePath) {
        return res.status(400).send("No image provided.");
    }

    const pythonProcess = spawn('python', ['detect_dress.py', imagePath]);

    let resultData = '';

    pythonProcess.stdout.on('data', (data) => {
        resultData += data.toString();
    });

    pythonProcess.on('close', () => {
        try {
            const parsedData = JSON.parse(resultData);
            res.render('detect', {
                imagePath,  // Send image path to render in detect.ejs
                detectedColor: parsedData.color,
                dressType: parsedData.dressType
            });
        } catch (error) {
            console.error("Error parsing JSON:", error);
            res.status(500).send("Failed to process image.");
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });
});

app.get('/getDressType', (req, res) => {
    const image = req.query.image;
    if (!image) {
        return res.status(400).json({ error: "No image provided." });
    }

    const imagePath = path.join(__dirname, 'uploads', image);
    
    // Call the Python script
    const pythonProcess = spawn('python', ['detect_dress.py', imagePath]);

    pythonProcess.stdout.on('data', (data) => {
        let dressType = data.toString().trim();

        // **Fix: Remove leading numbers and dots (e.g., "1. Pant" -> "Pant")**
        dressType = dressType.replace(/^\d+\.\s*/, "");

        res.json({ dressType });
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
        res.status(500).json({ error: "Error detecting dress type" });
    });
});

const rgbToHex = (r, g, b) => {
    return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`;
};

// Get Color Name from HEX
const namer = require('color-namer');

const getColorNameFromHex = (hexCode) => {
    try {
        const colorData = namer(hexCode);
        return colorData.ntc[0].name; // Uses 'Name That Color' dataset
    } catch (error) {
        return "Unknown Color";
    }
};

// Route to process color detection
app.post("/getColor", (req, res) => {
    const { r, g, b } = req.body;
    if (r === undefined || g === undefined || b === undefined) {
        return res.status(400).send("Invalid color data.");
    }

    const csvPath = 'reduced_color.csv';
    let closestColors = [];
    let minDistance = Infinity;

    fs.createReadStream(csvPath)
        .pipe(csv({ headers: ['color', 'color_name', 'hex', 'R', 'G', 'B', 'color_1', 'color_2', 'color_3', 'color_4', 'color_5'] }))
        .on('data', (row) => {
            const dr = Math.abs(r - row.R);
            const dg = Math.abs(g - row.G);
            const db = Math.abs(b - row.B);
            const distance = dr + dg + db;

            if (distance < minDistance) {
                minDistance = distance;
                closestColors = [];
            }

            if (distance === minDistance) {
                [row.color_1, row.color_2, row.color_3, row.color_4, row.color_5]
                    .filter(color => color) // Remove empty values
                    .forEach(colorGroup => {
                        closestColors.push(...colorGroup.split(',').map(c => c.trim())); // Properly split colors
                    });
            }
        })
        .on('end', () => {
            // Ensure unique colors and remove empty entries
            const uniqueColors = [...new Set(closestColors)].filter(c => c);

            // Convert hex codes to color names
            const colorData = uniqueColors.map(hex => ({
                hex,
                name: getColorNameFromHex(hex)
            }));

            // Convert detected RGB to hex & get color name
            const detectedHex = rgbToHex(r, g, b);
            const detectedColor = {
                hex: detectedHex,
                name: getColorNameFromHex(detectedHex)
            };

            console.log("Detected:", detectedColor);
            console.log("Matching Colors:", colorData);

            res.json({ detected: detectedColor, match: colorData });
        });
});

// Get Dress Type
app.get('/getDressType', (req, res) => {
    const image = req.query.image;
    if (!image) return res.status(400).json({ error: "No image provided." });

    const imagePath = path.join(__dirname, 'uploads', image);
    const pythonProcess = spawn('python', ['detect_dress.py', imagePath]);

    pythonProcess.stdout.on('data', (data) => {
        let dressType = data.toString().trim();
        res.json({ dressType });
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
        res.status(500).json({ error: "Error detecting dress type" });
    });
});

// Get Matching Dress from Amazon
app.get('/getDress', (req, res) => {
    const { color, dressType } = req.query;
    if (!color || !dressType) return res.status(400).json({ error: "Missing parameters" });

    const pythonProcess = spawn('python', ['fetch_dress.py', color, dressType]);

    let results = "";
    pythonProcess.stdout.on('data', (data) => { results += data.toString(); });

    pythonProcess.on('close', () => {
        try {
            const products = JSON.parse(results);
            res.json(products);
        } catch (err) {
            console.error(err);
            res.status(500).json({ error: "Error fetching products" });
        }
    }); 
});
app.get('/getAmazonResults', (req, res) => {
    const { color, dressType } = req.query;

    if (!color || !dressType) {
        return res.status(400).json({ error: "Color and dress type are required" });
    }

    const pythonProcess = spawn('python', ['amazon_scraper.py', color, dressType]);

    let resultData = '';

    pythonProcess.stdout.on('data', (data) => {
        resultData += data.toString();
    });

    pythonProcess.on('close', () => {
        try {
            const parsedData = JSON.parse(resultData);
            res.json(parsedData);
        } catch (error) {
            console.error("Error parsing JSON:", error);
            res.status(500).json({ error: "Failed to fetch Amazon data" });
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });
});