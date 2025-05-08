<?php
session_start();

// DB Connection
$conn = new mysqli("localhost", "root", "", "plastic_waste_management");
if ($conn->connect_error) die("Connection failed: " . $conn->connect_error);

$register_error = $login_error = "";
$register_success = "";

// Handle Registration
if ($_SERVER["REQUEST_METHOD"] == "POST" && $_POST['action'] == 'register') {
    $email = $_POST['reg_email'];
    $password = $_POST['reg_password'];

    // Check if user already exists
    $check = $conn->query("SELECT * FROM users WHERE email='$email'");
    if ($check->num_rows > 0) {
        $register_error = "Email already registered.";
    } else {
        $sql = "INSERT INTO users (email, password) VALUES ('$email', '$password')";
        if ($conn->query($sql)) {
            $register_success = "Registration successful! You can now log in.";
        } else {
            $register_error = "Error: " . $conn->error;
        }
    }
}

// Handle Login
if ($_SERVER["REQUEST_METHOD"] == "POST" && $_POST['action'] == 'login') {
    $email = $_POST['login_email'];
    $password = $_POST['login_password'];

    $sql = "SELECT * FROM users WHERE email='$email' AND password='$password'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $_SESSION['email'] = $email;
        header("Location: user-dashboard.php");
        exit();
    } else {
        $login_error = "Invalid email or password.";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>User Login & Register</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #a8e063, #56ab2f);
            color: white;
            display: flex;
            justify-content: space-around;
            align-items: flex-start;
            padding: 50px;
        }
        .form-box {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 10px;
            width: 320px;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }
        .form-box h2 {
            margin-bottom: 20px;
        }
        input {
            width: 90%;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 6px;
            border: none;
        }
        button {
            padding: 10px 20px;
            border: none;
            background: white;
            color: #2d6a4f;
            font-weight: bold;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.3s;
        }
        button:hover {
            background: #d9f99d;
        }
        p {
            color: yellow;
        }
    </style>
</head>
<body>

<div class="form-box">
    <h2>User Registration</h2>
    <?php if (!empty($register_error)) echo "<p>$register_error</p>"; ?>
    <?php if (!empty($register_success)) echo "<p>$register_success</p>"; ?>
    <form method="POST">
        <input type="hidden" name="action" value="register">
        <input type="email" name="reg_email" placeholder="Email" required><br>
        <input type="password" name="reg_password" placeholder="Password" required><br>
        <button type="submit">Register</button>
    </form>
</div>

<div class="form-box">
    <h2>User Login</h2>
    <?php if (!empty($login_error)) echo "<p>$login_error</p>"; ?>
    <form method="POST">
        <input type="hidden" name="action" value="login">
        <input type="email" name="login_email" placeholder="Email" required><br>
        <input type="password" name="login_password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
</div>

</body>
</html>
