export async function createSession(email: string, password: string, otp: string) {
  if (!email || !password || !otp) {
    throw new Error('missing credentials');
  }

  return {
    token: 'signed-token',
    internalUserId: 'user-123'
  };
}
