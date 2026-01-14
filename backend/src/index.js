require('dotenv').config();
const express = require('express');
const cors = require('cors');
const colors = require('colors');
const cp = require('cookie-parser');

const { connect } = require('./config/db');

const userRouter = require('./routes/user.routes');

const app = express();

app.use(express.json());
app.use(cors());
app.use(cp());

app.use('/api/user', userRouter);

connect()
    .then(() => {
        console.log("Connected to database".cyan);
        app.listen(process.env.PORT, () => {
            console.log(`Server running on port ${process.env.PORT}`.magenta);
        });
    })
    .catch((err) => console.log("Database connection failed".red, err));