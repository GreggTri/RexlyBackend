const mongoose = require('mongoose')

const UrlSchema = new mongoose.Schema({
    long: {type: String, required: true},
    short: {type: String, required: true, unique: true}

}, {timestamps: {
    createdAt: 'created_at'
}})

module.exports = mongoose.model('urls', UrlSchema)