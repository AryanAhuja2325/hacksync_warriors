const Prompt = require("../models/prompt.model");

exports.getInput = async (req, res) => {
  try {
    const { input } = req.body;

    const prompt = await Prompt.create({ input });

    res.json({
      msg: "Input stored",
      promptId: prompt._id,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getOutput = async (req, res) => {
  try {
    const { promptId, output } = req.body;

    const prompt = await Prompt.findByIdAndUpdate(
      promptId,
      { output },
      { new: true }
    );

    res.json({
      msg: "Output stored",
      prompt,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
