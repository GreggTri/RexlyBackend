const mongoose = require('mongoose')

const MessageSchema = new mongoose.Schema({
    user_id: {type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true},
    user_msg: {type: String, required: true},
    tag: {type: String, required: true},
    bot_response: {type: String, required: true},
    probability_response: {type: String},
    createdAt: { type: Date, default: Date.now, required: true }
})

module.exports = mongoose.model('messages', MessageSchema)