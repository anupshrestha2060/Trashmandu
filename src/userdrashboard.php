<?php
session_start();
if (!isset($_SESSION['username']) || $_SESSION['role'] != 'user') {
    header("Location: login.html");
    exit();
}
?>
<!DOCTYPE html>
<html>
<head><title>User Dashboard</title></head>
<body>
    <h2>Welcome, <?php echo $_SESSION['username']; ?> (User)</h2>
    <p>This is the user dashboard.</p>
    <a href="logout.php">Logout</a>
</body>
</html>
