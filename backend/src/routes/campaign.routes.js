const express = require("express");
const router = express.Router();

const campaignController = require("../controllers/campaign.controller");
const auth = require("../middleware/auth.middleware");
const upload = require("../middleware/upload");

router.post(
  "/upload-prompt",
  auth({ optional: true }), // Make auth optional for testing
  upload.single("file"), // optional PDF upload
  campaignController.createCampaign
);

// Get all campaigns of logged-in user
router.get("/", auth(), campaignController.getMyCampaigns);

// Get single campaign
router.get(
  "/:id",
  auth(),
  campaignController.getCampaignById
);

// Add agent output (FastAPI / worker callback)
router.post(
  "/:campaignId/agent",
  campaignController.addAgentResult
);

// Update campaign status
router.patch(
  "/:campaignId/status",
  campaignController.updateCampaignStatus
);

module.exports = router;
