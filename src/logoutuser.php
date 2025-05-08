<?php
session_start();
if (!isset($_SESSION['email'])) {
    header("Location: user-login.php");
    exit();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>User Dashboard</title>
    <style>
        body {
            background: linear-gradient(to right, #a8e063, #56ab2f);
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding-top: 100px;
        }
        a {
            color: white;
            font-weight: bold;
            text-decoration: none;
            padding: 10px 20px;
            border: 2px solid white;
            border-radius: 8px;
            background-color: rgba(255,255,255,0.1);
            transition: background 0.3s;
        }
        a:hover {
            background: #d9f99d;
            color: #2d6a4f;
        }
    </style>
</head>
<body>
    <h2>Welcome, <?php echo $_SESSION['email']; ?>!</h2>
    <a href="logout.php">Logout</a>
</body>
</html>
