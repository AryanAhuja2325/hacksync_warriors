const mongoose = require("mongoose");

const otpSchema = new mongoose.Schema({
    email: { type: String, required: true },
    otp: { type: String, required: true },

    purpose: {
        type: String,
        enum: ["REGISTER", "LOGIN", "FORGOT_PASSWORD"],
        required: true
    },

    payload: {
        name: String,
        password: String,
        role: String
    },

    expiresAt: { type: Date, required: true },
    used: { type: Boolean, default: false }
}, { timestamps: true });

otpSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

module.exports = mongoose.model("OTP", otpSchema);