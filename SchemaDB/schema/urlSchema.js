const mongoose = require('mongoose')

const UrlSchema = new mongoose.Schema({
    user_id: {type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true},
    long: {type: String, required: true},
    short: {type: String, required: true, unique: true},
    createdAt: { type: Date, default: Date.now, required: true }
})

module.exports = mongoose.model('urls', UrlSchema)