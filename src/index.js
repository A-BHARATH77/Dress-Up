const express=require('express');
const path = require('path');
const crypt=require("bcrypt");
const collection=require ('./config');

const app=express();
app.set('view engine','ejs');
app.use(express.static("public"));
app.use(express.json());
app.use(express.urlencoded({extended:false}));

const port= 5000
app.listen(port,()=>{
    console.log(`Server runnning on port:${port}`);
})

app.get("/",(req,res)=>{
    res.render("login");
})

app.get("/signup",(req,res)=>{
    res.render("signup");
})


app.post("/signup", async (req, res) =>{
    const data = {
            name: req.body.username,
            password: req.body.password
    }
    const existinguser= await collection.findOne({name:data.name});
    if(existinguser){
        res.send("User already exists.Please choose different username.");
    }else{
        const saltrounds=10;
        const hashedpass=await crypt.hash(data.password,saltrounds);
        data.password=hashedpass;
    const userdata = await collection.insertMany (data);
    console.log(userdata);
    res.render("home")
    }
});

    app.post("/login", async (req, res) => {
        try{
        const check=await collection.findOne({name: req.body.username}); 
        if(!check) {
        res.send("user name cannot be found");
        return;
        }
        const isPasswordMatch =await crypt.compare(req.body.password, check.password); 
        if(isPasswordMatch) {
        res.render("home");
        }else {
            req.send("wrong password");
        } 
        }  
        catch(error){
            console.error(error);
            res.status(500).send("An error occurred while logging in");
        }
    });