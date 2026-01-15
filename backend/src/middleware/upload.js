// const multer = require("multer");

// const storage = multer.memoryStorage();

// const upload = multer({
//   storage,
//   limits: { fileSize: 5 * 1024 * 1024 },
// });

// module.exports = upload;
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = path.join(__dirname, '../../tempUploads');
        try {
            fs.mkdirSync(uploadDir, { recursive: true });
        } catch (err) {
            // ignore mkdir errors and let multer handle if necessary
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const uniqueName = `${Date.now()}-${file.originalname}`;
        cb(null, uniqueName);
    },
});

const fileFilter = (req, file, cb) => {
    const allowedTypes = [
        'application/pdf',
    ];
    if (!allowedTypes.includes(file.mimetype)) {
        return cb(new Error('Only PDF files are allowed!'), false);
    }
    cb(null, true);
};

const upload = multer({ storage, fileFilter });

module.exports = upload;