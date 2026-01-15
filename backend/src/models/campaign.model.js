const mongoose = require("mongoose");

const inputSchema = new mongoose.Schema({
  type: {
    type: String,
    enum: ["text", "pdf"],
    required: true
  },
  value: {
    type: String,
    required: true // text OR pdf URL
  }
}, { _id: false });

const agentOutputSchema = new mongoose.Schema({
  agentName: { type: String, required: true },
  result: { type: mongoose.Schema.Types.Mixed, required: true }
}, { _id: false });

const campaignSchema = new mongoose.Schema({
  email: {type: mongoose.Schema.Types.ObjectId, required: true, ref: 'User'},
  input: { type: inputSchema, required: true },

  strategy: { type: mongoose.Schema.Types.Mixed },

  agents: { type: [agentOutputSchema], default: [] },

  status: {
    type: String,
    enum: ["pending", "processing", "completed", "failed"],
    default: "processing"
  },

  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Campaign", campaignSchema);
