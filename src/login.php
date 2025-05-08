<?php
session_start();
include("db_config.php");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = mysqli_real_escape_string($conn, $_POST["username"]);
    $password = $_POST["password"];
    $role = mysqli_real_escape_string($conn, $_POST["role"]);

    $query = "SELECT * FROM users WHERE username='$username' AND role='$role'";
    $result = mysqli_query($conn, $query);

    if (mysqli_num_rows($result) == 1) {
        $user = mysqli_fetch_assoc($result);

        // Simple password check (for now, no hashing)
        if ($user['password'] == $password) {
            $_SESSION['username'] = $user['username'];
            $_SESSION['role'] = $user['role'];

            // Redirect to dashboard based on role
            if ($role == "user") {
                header("Location: user_dashboard.php");
                exit();
            } elseif ($role == "collector") {
                header("Location: collector_dashboard.php");
                exit();
            } elseif ($role == "admin") {
                header("Location: admin_dashboard.php");
                exit();
            }
        } else {
            echo "❌ Incorrect password!";
        }
    } else {
        echo "❌ Invalid username or role!";
    }
}
?>
