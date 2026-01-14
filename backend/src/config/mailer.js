const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
    host: "smtp.gmail.com",
    port: 465,
    secure: true,
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
    },
});

const sendMail = async ({ to, subject, html }) => {
    try {
        const info = await transporter.sendMail({
            from: `"Appointment App" <${process.env.EMAIL_USER}>`,
            to,
            subject,
            html,
        });

        console.log("Email sent:", info.messageId);
        return true;
    } catch (error) {
        console.error("Email sending failed:", error);
        return false;
    }
};

const sendOTPEmail = async (email, otp, purpose) => {
    return sendMail({
        to: email,
        subject: `OTP for ${purpose}`,
        html: `
            <div style="font-family: Arial">
                <h2>Your OTP</h2>
                <h1>${otp}</h1>
                <p>This OTP is valid for 10 minutes.</p>
                <small>If you didn’t request this, ignore the email.</small>
            </div>
        `
    });
};

module.exports = {
    sendMail,
    sendOTPEmail
};