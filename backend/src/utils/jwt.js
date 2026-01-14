const jwt = require("jsonwebtoken");

const createToken = (user) => {
  return jwt.sign(
    { id: user._id, email: user.email },
    process.env.SECRET_KEY,
    { expiresIn: "3d" }
  );
};

module.exports = createToken;
