<!DOCTYPE html>
<html lang="en">
<head><title>DinoSaurch</title>
    <style>
        h1 {color: #20B2AA; text-align: center; padding-top: 120px; font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;}
        form {color: #20B2AA; text-align: center; font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;}
        input[type=text] {width: 25%;-moz-border-radius: 5px;-webkit-border-radius: 5px;}
        input[type=submit] {width: 6%;height: 3%; color: #87CEEB;background-color: #4682B4;border: none;-moz-border-radius: 5px;-webkit-border-radius: 5px;}
        h2 {text-align: center;}
        p {text-align: center;}
        table{float: left; width:148px; padding-top: 0.5cm;}
        #table_container{width:450px;  top: 0; bottom: 0; left: 0; right:0; margin: auto; height:auto;}
        td {padding: 1px; text-align: center;}
        .logo {position: absolute; top: 0; left: 0; right:0; margin: auto;width:108px;height:120px;}
        .profile {float: right;}
        .profile-image {width:50px;height:50px;}
        ul {list-style-type: none; margin: 0; padding: 0; text-align: right;  position:relative; display: inline-block;}
    </style>
</head>
<body>
    % if anonymous == False:
        <div class="profile">
        <ul><li><a title="sign out" href="/signout" >Sign out</a></li>
        <img src ="{{picture}}" class="profile-image">
        <li>{{name}}</li>
        <li>{{email}}</li></ul></div>
    % else:
        <a style="float:right"; title="sign in" href="/login" >Sign in</a>
    % end
        <div><img src="/static/logo.jpg" class="logo" alt="DinoSaurch">
        <h1>DinoSaurch</h1>
        <form action ="/search" method="get">
             Search: <input name="keywords" type="text"/>
                    <input value = "Search" type="submit"/>
        </form></div>
</body>
</html>
