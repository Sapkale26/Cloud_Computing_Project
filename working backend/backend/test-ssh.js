const { NodeSSH } = require("node-ssh");
const ssh = new NodeSSH();

ssh
  .connect({
    host: "192.168.50.1",
    username: "pi",
    password: "1234",
    readyTimeout: 10000,
  })
  .then(async () => {
    console.log("Connected!");
    const result = await ssh.execCommand("uptime");
    console.log("Result:", result.stdout);
    ssh.dispose();
  })
  .catch((err) => {
    console.log("Error:", err.message);
  });
