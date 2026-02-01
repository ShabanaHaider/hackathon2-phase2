import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
// change revert for running app on vercel
export const { GET, POST } = toNextJsHandler(auth.handler);
// export const { GET, POST } = toNextJsHandler(auth);