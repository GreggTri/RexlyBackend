const mongoose = require('mongoose')

const UserSchema = new mongoose.Schema({
    email: {type: String, required: true, unique: true},
    phoneNumber: {type: String, required: true, unique: true},
    password: {type: String, required: true, unique: true}
})

UserSchema.set('timestamps', true)
module.exports = mongoose.model('users', UserSchema)