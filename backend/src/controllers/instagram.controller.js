// Instagram controller removed - functionality has been removed from the application
module.exports = {
  postToInstagram: (req, res) => res.status(410).json({ msg: 'Instagram posting endpoint removed' })
};
