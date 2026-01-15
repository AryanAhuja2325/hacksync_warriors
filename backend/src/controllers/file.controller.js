const {bucket} = require("../config/firebase");
const fs=require('fs')
exports.uploadPDF = async (req, res) => {
  try {
    if (!req.file) {
            return res.status(400).json({ success: false, error: 'No file uploaded' });
        }

        const fileName = `job_descriptions/${Date.now()}_${req.file.originalname}`;
        const file = bucket.file(fileName);

        const fileBuffer = req.file.buffer || fs.readFileSync(req.file.path);

        await file.save(fileBuffer, {
            contentType: req.file.mimetype,
            metadata: { firebaseStorageDownloadTokens: Date.now().toString() },
        });

        const fileUrl = `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(
            fileName
        )}?alt=media`;
        res.json({ url: fileUrl });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
