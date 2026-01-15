const express = require('express');
const { analyzeCompetitor } = require('../controllers/competitor.controller');
const authMiddleware = require('../middleware/auth.middleware');

const router = express.Router();

// POST /api/competitors/analyze - Analyze competitor websites
router.post('/analyze', authMiddleware, analyzeCompetitor);

module.exports = router;
