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
const promptRoutes=require('./routes/prompt.routes')
const competitorRoutes=require('./routes/competitor.routes')
const instagramRoutes=require('./routes/instagram.routes')

const app=express()

app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true
}))

app.use(express.json())
app.use(passport.initialize())

app.use(cp());

app.use('/auth',authRoutes)
app.use("/files", fileRoutes);
app.use('/prompt',promptRoutes)
app.use('/api/competitors',competitorRoutes)
app.use('/api/instagram',instagramRoutes)

app.listen(5000,()=>{
    console.log("Server Running on Port 5000")
})
