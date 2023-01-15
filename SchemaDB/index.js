const mongoose = require('mongoose')
const usersModel = require('./schema/userSchema')
const messagesModel = require('./schema/messageSchema')
const urlsModel = require('./schema/urlSchema')
require('dotenv').config()

//Connects to database
mongoose.set('strictQuery', true)
mongoose.connect(process.env.MONGO_URL, { useNewUrlParser:true})
.then(
    () => { 
        //compiles models
        console.log("Database connected");
        const users = usersModel
        const messages = messagesModel
        const urls = urlsModel
        const db = mongoose.models

        console.log(db);
    },
    err => { 
        /** handle initial connection error */ 
        console.log("Error in database connection. ", err);
    }
);
