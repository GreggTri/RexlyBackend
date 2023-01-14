const mongoose = require('mongoose')
const userSchema = require('./schema/userSchema')
const messageSchema = require('./schema/messageSchema')
require('dotenv').config()

//Connects to database
mongoose.set('strictQuery', true)
mongoose.connect(process.env.MONGO_URL, { useNewUrlParser:true})
.then(
    () => { 
        //compiles models
        console.log("Database connected");
        const db = mongoose.models
        console.log(db);
    },
    err => { 
        /** handle initial connection error */ 
        console.log("Error in database connection. ", err);
    }
);
