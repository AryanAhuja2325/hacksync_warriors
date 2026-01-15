const Campaign = require("../models/campaign.model");
const { bucket } = require("../config/firebase");
const fs = require("fs");

exports.createCampaign = async (req, res) => {
  try {
    // console.log("trying");
    let input;

    /**
     * TEXT INPUT
     */
    if (req.body.text) {
      input = {
        type: "text",
        value: req.body.text
      };
    }

    /**
     * PDF INPUT
     */
    if (req.file) {
      const localPath = req.file.path;
      const fileName = `campaign_pdfs/${Date.now()}_${req.file.originalname}`;

      await bucket.upload(localPath, {
        destination: fileName,
        metadata: { contentType: req.file.mimetype }
      });

      const pdfUrl = `https://storage.googleapis.com/${bucket.name}/${fileName}`;

      fs.unlinkSync(localPath);

      input = {
        type: "pdf",
        value: pdfUrl
      };
    }

    if (!input) {
      return res.status(400).json({
        message: "Either text or PDF is required"
      });
    }

    /**
     * DUMMY STRATEGY (to be replaced by agent later)
     */
    const dummyStrategy = {
      product: "Unknown",
      audience: "General",
      goal: "Brand Awareness",
      generatedBy: "strategy-agent",
      generatedAt: new Date()
    };

    const campaign = await Campaign.create({
      email: req.user._id,
      input,
      strategy: dummyStrategy,
      status: "processing"
    });

    res.status(201).json({
      success: true,
      campaignId: campaign._id,
      input,
      strategy: dummyStrategy
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({
      message: "Campaign creation failed"
    });
  }
};

/**
 * Add / Update agent output
 */
exports.addAgentResult = async (req, res) => {
  try {
    const { campaignId } = req.params;
    const { agentName, result } = req.body;

    if (!agentName || !result) {
      return res.status(400).json({ message: "Agent name and result required" });
    }

    const campaign = await Campaign.findById(campaignId);
    if (!campaign) {
      return res.status(404).json({ message: "Campaign not found" });
    }
    campaign.agents.push({ agentName, result });
    await campaign.save();

    res.json({ success: true, campaign });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to add agent result" });
  }
};

/**
 * Mark campaign status
 */
exports.updateCampaignStatus = async (req, res) => {
  try {
    const { campaignId } = req.params;
    const { status } = req.body;

    const campaign = await Campaign.findByIdAndUpdate(
      campaignId,
      { status },
      { new: true }
    );

    if (!campaign) {
      return res.status(404).json({ message: "Campaign not found" });
    }

    res.json({ success: true, campaign });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to update status" });
  }
};

/**
 * Get all campaigns of logged-in user
 */
exports.getMyCampaigns = async (req, res) => {
  try {
    const campaigns = await Campaign.find({ email: req.user._id })
      .sort({ createdAt: -1 });

    res.json({ success: true, campaigns });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to fetch campaigns" });
  }
};

/**
 * Get single campaign
 */
exports.getCampaignById = async (req, res) => {
  try {
    const campaign = await Campaign.findOne({
      _id: req.params.id,
      email: req.user._id
    });

    if (!campaign) {
      return res.status(404).json({ message: "Campaign not found" });
    }

    res.json({ success: true, campaign });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Failed to fetch campaign" });
  }
};
