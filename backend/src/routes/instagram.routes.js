// Instagram routes removed
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.status(410).json({ msg: 'Instagram endpoints removed' });
});

module.exports = router;
