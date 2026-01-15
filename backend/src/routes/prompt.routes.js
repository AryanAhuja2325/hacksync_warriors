const express=require('express')
const {getInput,getOutput}=require('../controllers/prompt.controller')

const router=express.Router()
router.post("/input", getInput);
router.post("/output", getOutput);

module.exports = router;
