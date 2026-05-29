import { Router } from 'express';
import { createSession } from './session_service';

export const router = Router();

router.post('/login', async (req, res) => {
  const session = await createSession(req.body.email, req.body.password, req.body.otp);
  res.json({ token: session.token, internalUserId: session.internalUserId });
});
