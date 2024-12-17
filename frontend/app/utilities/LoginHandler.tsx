import { Authenticator } from "remix-auth";
import { FormStrategy } from "remix-auth-form";
import { User } from "~/data";

import { createCookieSessionStorage } from "@remix-run/node";
import { MAX_SESSION_AGES } from "~/config";

// export the whole sessionStorage object
export const sessionStorage = createCookieSessionStorage({
  cookie: {
    name: "_session", // use any name you want here
    sameSite: "lax", // this helps with CSRF
    maxAge: MAX_SESSION_AGES, // 5 minutes
    path: "/", // remember to add this so the cookie will work in all routes
    httpOnly: true, // for security reasons, make this cookie http only
    secrets: ["s3cr3t"], // replace this with an actual secret
    secure: process.env.NODE_ENV === "production", // enable this in prod only
  },
});

// you can also export the methods individually for your own usage
export const { getSession, commitSession, destroySession } = sessionStorage;

export let authenticator = new Authenticator<User>();

// Tell the Authenticator to use the form strategy
authenticator.use(
  new FormStrategy(async ({ form }) => {
    const name = form.get("username")?.toString() ?? "";
    const password = form.get("password")?.toString() ?? "";
    // the type of this user must match the type you pass to the Authenticator
    // the strategy will automatically inherit the type if you instantiate
    // directly inside the `use` method

    // TODO: Build this User from a database function...
    const user: User = {
      id: 1,
      username: name,
      password: password,
    };

    // Example login data, no backend is connected.
    if (!(user.username === "admin" && user.password === "admin"))
      throw new Error("Invalid username or password");

    return user;
  }),
  // each strategy has a name and can be changed to use another one
  // same strategy multiple times, especially useful for the OAuth2 strategy.
  "user-pass"
);
