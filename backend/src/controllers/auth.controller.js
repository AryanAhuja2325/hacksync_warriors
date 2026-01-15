const bcrypt = require("bcryptjs");
const User = require("../models/user.model");
const createToken = require("../utils/jwt");

const signup = async (req, res) => {
  try {
    const { email, password } = req.body;
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ msg: "Email already registered" });
    }
    const hash = await bcrypt.hash(password, 10);
    const user = await User.create({ email, password: hash });

    const token = createToken(user);
    const { password: _, ...userData } = user._doc;

    res.json({ token, user: userData });
  } catch (err) {
    res.status(500).json({ msg: "Signup failed", error: err.message });
  }
};

const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ msg: "User not found" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ msg: "Wrong password" });
    const token = createToken(user);

    const { password: _, ...userData } = user._doc;

    res.cookie('token', token, {
      maxAge: 900000, // Cookie expires after 15 minutes (in milliseconds)
      httpOnly: true, // Makes the cookie inaccessible to client-side JavaScript (security best practice)
      secure: true,   // Ensures the cookie is only sent over HTTPS (set to false for localhost testing with HTTP)
    });

    res.json({user: userData });
  } catch (err) {
    res.status(500).json({ msg: "Login failed", error: err.message });
  }
};

module.exports = { signup, login };
