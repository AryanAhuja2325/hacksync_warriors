const express = require("express");
const upload = require("../middleware/upload");
const { uploadPDF } = require("../controllers/file.controller");

const router = express.Router();

router.post("/upload", upload.single("file"), uploadPDF);

module.exports = router;
