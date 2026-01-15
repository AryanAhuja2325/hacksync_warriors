const express = require('express');
const router = express.Router();
const { postToInstagram } = require('../controllers/instagram.controller');
const { getAccountInsights } = require('../controllers/insights.controller');
const authMiddleware = require('../middleware/auth.middleware');

// POST /api/instagram/post
router.post('/post', authMiddleware, postToInstagram);

// GET /api/instagram/insights
router.get('/insights', authMiddleware, getAccountInsights);

module.exports = router;
