const User = require("../models/user.model");
const OTP = require('../models/otp.model');
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const { sendMail, sendOTPEmail } = require('../config/mailer');
const { generateOTP } = require('../utils/misc');

async function register(req, res) {
    try {
        const { name, email, password } = req.body;
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ message: "Email already exists" });
        }
        await OTP.deleteMany({ email, purpose: "REGISTER", used: false });
        const otp = generateOTP();

        await OTP.create({
            email,
            otp,
            purpose: "REGISTER",
            payload: {
                name,
                password
            },
            expiresAt: Date.now() + 10 * 60 * 1000
        });

        await sendOTPEmail(email, otp, "Registration");

        res.status(200).json({
            message: "OTP sent to email. Verify to complete registration"
        });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}
async function verifyRegisterOTP(req, res) {
    try {
        const { email, otp } = req.body;

        const otpDoc = await OTP.findOne({
            email,
            otp,
            purpose: "REGISTER",
            used: false,
            expiresAt: { $gt: Date.now() }
        });

        if (!otpDoc) {
            return res.status(400).json({ message: "Invalid or expired OTP" });
        }

        const { name, password } = otpDoc.payload;

        const user = await User.create({
            name,
            email,
            password,
        });

        otpDoc.used = true;
        await otpDoc.save();

        res.status(201).json({
            message: "User registered successfully",
            userId: user._id
        });

    } catch (err) {
        console.log(err)
        res.status(500).json({ error: err.message });
    }
}

async function login(req, res) {
    try {
        const { email, password, loginType } = req.body;

        const user = await User.findOne({ email });
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        if (loginType === "PASSWORD" || password) {

            if (!password) {
                return res.status(400).json({ message: "Password required" });
            }

            const isMatch = await bcrypt.compare(password, user.password);
            if (!isMatch) {
                return res.status(401).json({ message: "Invalid credentials" });
            }

            const token = jwt.sign(
                { id: user._id },
                process.env.SECRET_KEY,
                { expiresIn: "7d" }
            );

            res.cookie("token", token)

            return res.status(200).json({
                message: "Login successful",
                user: {
                    id: user._id,
                    name: user.name,
                    email: user.email
                }
            });
        }

        /* 🔹 OTP LOGIN */
        if (loginType === "OTP") {

            // clear previous unused OTPs
            await OTP.deleteMany({ email, purpose: "LOGIN", used: false });

            const otp = generateOTP();

            await OTP.create({
                userId: user._id,
                email,
                otp,
                purpose: "LOGIN",
                expiresAt: Date.now() + 10 * 60 * 1000
            });

            await sendOTPEmail(email, otp, "Login");

            return res.status(200).json({
                message: "OTP sent to email"
            });
        }

        res.status(400).json({ message: "Invalid login request" });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}


async function verifyLoginOTP(req, res) {
    try {
        const { email, otp } = req.body;

        const otpDoc = await OTP.findOne({
            email,
            otp,
            purpose: "LOGIN",
            used: false,
            expiresAt: { $gt: Date.now() }
        });

        if (!otpDoc) {
            return res.status(400).json({ message: "Invalid or expired OTP" });
        }

        const user = await User.findOne({ email: otpDoc.email });

        otpDoc.used = true;
        await otpDoc.save();

        const token = jwt.sign(
            { id: user._id },
            process.env.SECRET_KEY,
            { expiresIn: "7d" }
        );

        res.cookie('token', token);

        res.status(200).json({
            message: "Login successful",
            user: {
                id: user._id,
                name: user.name,
                email: user.email
            }
        });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}

async function getProfile(req, res) {
    try {
        const user = await User.findById(req.user._id).select("-password");
        res.status(200).json(user);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}

async function updateProfile(req, res) {
    try {
        const { name } = req.body;

        await User.findByIdAndUpdate(req.user._id, { name });
        res.status(200).json({ message: "Profile updated" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}

async function changePassword(req, res) {
    try {
        const { oldPassword, newPassword } = req.body;

        const user = await User.findById(req.user.id);
        if (!user) return res.status(404).json({ error: "User not found" });

        const isMatch = await user.comparePassword(oldPassword);
        if (!isMatch) return res.status(400).json({ error: "Incorrect old password" });

        user.password = newPassword;
        await user.save();

        res.status(200).json({ message: "Password updated" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}

async function forgotPassword(req, res) {
    try {
        const { email } = req.body;

        if (!email) {
            return res.status(400).json({ message: "Email is required" });
        }

        const user = await User.findOne({ email });
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        // Delete old unused OTPs
        await OTP.deleteMany({
            email,
            purpose: "FORGOT_PASSWORD",
            used: false
        });

        const otp = generateOTP();

        await OTP.create({
            email,
            otp,
            purpose: "FORGOT_PASSWORD",
            expiresAt: Date.now() + 10 * 60 * 1000 // 10 min
        });

        await sendOTPEmail(email, otp, "Password Reset");

        res.status(200).json({
            message: "OTP sent to email for password reset"
        });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}

async function resetPassword(req, res) {
    try {
        const { email, otp, newPassword } = req.body;

        if (!email || !otp || !newPassword) {
            return res.status(400).json({ message: "All fields are required" });
        }

        const otpDoc = await OTP.findOne({
            email,
            otp,
            purpose: "FORGOT_PASSWORD",
            used: false,
            expiresAt: { $gt: Date.now() }
        });

        if (!otpDoc) {
            return res.status(400).json({ message: "Invalid or expired OTP" });
        }

        const user = await User.findOne({ email });
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        user.password = newPassword;
        await user.save();

        otpDoc.used = true;
        await otpDoc.save();

        res.status(200).json({
            message: "Password reset successful"
        });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}


module.exports = {
    register,
    verifyRegisterOTP,
    login,
    verifyLoginOTP,
    getProfile,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword
};