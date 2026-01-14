const mongoose=require('mongoose')

const promptsSchema=new mongoose.Schema({
     input: { type: String, required: true },
    output: { type: String },
})

module.exports=mongoose.model('Prompts',promptsSchema)