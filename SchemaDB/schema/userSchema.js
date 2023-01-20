const mongoose = require('mongoose')

const UserSchema = new mongoose.Schema({
    email: {type: String, required: true, unique: true},
    phoneNumber: {type: String, required: true, unique: true},
    password: {type: String, required: true, unique: true},
    created_At: { type: Date, default: Date.now}
}, {
    timestamps: true
  })
module.exports = mongoose.model('users', UserSchema)