<!DOCTYPE html>
<html>
<head>
    <title>Trashmandu - Plastic Waste Management System</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(to right, #a8e063, #56ab2f);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: white;
            text-align: center;
        }

        .container {
            max-width: 800px;
            padding: 20px;
        }

        h1 {
            font-size: 3rem;
            margin-bottom: 20px;
        }

        p.intro {
            font-size: 1.2rem;
            margin-bottom: 25px;
        }

        blockquote {
            font-style: italic;
            font-size: 1.1rem;
            color: #fefae0;
            margin: 20px 0;
        }

        .role-buttons {
            display: flex;
            gap: 40px;
            justify-content: center;
            margin-top: 30px;
        }

        .role {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .role img {
            width: 80px;
            height: 80px;
            margin-bottom: 10px;
            background-color: white;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }

        .role button {
            padding: 12px 25px;
            font-size: 16px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            background-color: white;
            color: #2d6a4f;
            font-weight: bold;
            transition: background-color 0.3s;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
        }

        .role button:hover {
            background-color: #d9f99d;
        }

        footer {
            margin-top: 40px;
            font-size: 0.9rem;
            color: #e0f2e9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Trashmandu</h1>
        <p class="intro">
            A cleaner future, one bottle at a time. Please select your role to log in:
        </p>
        <blockquote>“The Earth is what we all have in common.”</blockquote>

        <div class="role-buttons">
            <div class="role">
                <img src="image/user.png" alt="User Icon">
                <form action="login.html" method="get">
                    <input type="hidden" name="role" value="user">
                    <button type="submit">User</button>
                </form>
            </div>

            <div class="role">
                <img src="image/download.png" alt="Collector Icon">
                <form action="login.html" method="get">
                    <input type="hidden" name="role" value="collector">
                    <button type="submit">Collector</button>
                </form>
            </div>

            <div class="role">
                <img src="image/admin.png" alt="Admin Icon">
                <form action="login.html" method="get">
                    <input type="hidden" name="role" value="admin">
                    <button type="submit">Admin</button>
                </form>
            </div>
        </div>

        <footer>© 2025 Trashmandu - Plastic Waste Management System</footer>
    </div>
</body>
</html>
