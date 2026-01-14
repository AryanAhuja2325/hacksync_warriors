const express = require("express");
const userRouter = express.Router();

const {
    register,
    verifyRegisterOTP,
    login,
    verifyLoginOTP,
    getProfile,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword
} = require("../controllers/user.controller");

const auth = require("../middleware/auth.middleware");

userRouter.post("/register", register);

userRouter.post("/register/verify-otp", verifyRegisterOTP);

userRouter.post("/login", login);

userRouter.post("/login/verify-otp", verifyLoginOTP);

userRouter.get("/profile", auth(), getProfile);
userRouter.put("/profile", auth(), updateProfile);
userRouter.put("/change-password", auth(), changePassword);

userRouter.post('/forgot-password', forgotPassword);
userRouter.post('/forgot-password/verify-otp', resetPassword)

module.exports = userRouter;