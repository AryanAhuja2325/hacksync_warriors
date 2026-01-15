require("dotenv").config();
const express=require("express")
const cors=require("cors")
const passport=require("passport")
const connect=require('./config/db')
const cp = require('cookie-parser');

connect().then(() => {
    app.listen(5000,()=>{
        console.log("Server Running on Port 5000")
    })
})

// require("./passport")

const authRoutes=require('./routes/auth.routes')
const fileRoutes=require('./routes/file.routes')
const campaignRoutes=require('./routes/campaign.routes')
const app=express()

app.use(cors())

app.use(express.json())
app.use(passport.initialize())

app.use(cp());

app.use('/auth',authRoutes)
app.use("/files", fileRoutes);
app.use('/campaign',campaignRoutes)
