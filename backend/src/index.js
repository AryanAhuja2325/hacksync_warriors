require("dotenv").config();
const express=require("express")
const cors=require("cors")
const passport=require("passport")
const connect=require('./config/db')
connect()
// require("./passport")
const authRoutes=require('./routes/auth.routes')
const competitorRoutes=require('./routes/competitor.routes')

const app=express()

app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true
}))

app.use(express.json())
app.use(passport.initialize())

app.use('/auth',authRoutes)
app.use('/api/competitors',competitorRoutes)

app.listen(5000,()=>{
    console.log("Server Running on Port 5000")
})