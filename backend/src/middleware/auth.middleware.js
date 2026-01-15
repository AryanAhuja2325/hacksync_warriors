const jwt = require("jsonwebtoken");
const User = require("../models/user.model");

const authMiddleware = async (req, res, next) => {
    try {
        // Get token from Authorization header (Bearer token)
        const authHeader = req.headers.authorization;
        
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ msg: "No token, authorization denied" });
        }

        const token = authHeader.split(' ')[1];
        
        if (!token) {
            return res.status(401).json({ msg: "No token, authorization denied" });
        }

        // Verify token
        const decoded = jwt.verify(token, process.env.SECRET_KEY);

        if (!decoded?.id) {
            return res.status(401).json({ msg: "Invalid token" });
        }

        // Get user from database
        const user = await User.findById(decoded.id).select('-password');
        
        if (!user) {
            return res.status(401).json({ msg: "User not found" });
        }

        req.user = user;
        next();
    } catch (err) {
        console.error('Auth middleware error:', err.message);
        return res.status(401).json({ msg: "Token is not valid" });
    }
};

module.exports = authMiddleware;