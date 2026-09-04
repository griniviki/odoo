const express = require("express");

const app = express();
const port = 8081;

app.get("/odata/A_BusinessPartner", (req, res) => {
    res.json({
        value: [
            {
                BusinessPartner: "BP001",
                FirstName: "Me",
                LastName: "Me"
            },
            {
                BusinessPartner: "BP002",
                FirstName: "Anna",
                LastName: "Example"
            }
        ]
    });
});

app.listen(port, "0.0.0.0", () => {
    console.log(`Mock SAP server running on port ${port}`);
});

app.use(express.json());

app.post("/odata/A_BusinessPartner", (req, res) => {
    console.log("Received:", req.body);

    res.status(201).json({
        message: "Business Partner created",
        value: req.body
    });
});