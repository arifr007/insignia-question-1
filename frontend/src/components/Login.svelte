<script>
  import { auth, loading, error } from '../stores/index.js';
  import Card from './ui/Card.svelte';
  import Button from './ui/Button.svelte';
  import Input from './ui/Input.svelte';
  import FormField from './ui/FormField.svelte';
  import Alert from './ui/Alert.svelte';

  let isLogin = true;
  let username = '';
  let password = '';

  async function handleSubmit() {
    if (isLogin) {
      const success = await auth.login(username, password);
      if (!success) return;
    } else {
      const success = await auth.register(username, password);
      if (success) {
        isLogin = true;
        username = '';
        password = '';
        $error = null;
      }
    }
  }

  function toggleMode() {
    isLogin = !isLogin;
    $error = null;
  }
</script>

<div class="min-h-screen flex items-center justify-center p-4">
  <div class="w-full max-w-md">
    <Card variant="elevated">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-400">Finance Analytics</h1>
        <p class="text-gray-300 mt-2">
          {isLogin ? 'Sign in to your account' : 'Create a new account'}
        </p>
      </div>

      <Alert message={$error} type="error" />

      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <FormField label="Username" required id="username">
          <Input
            id="username"
            type="text"
            bind:value={username}
            placeholder="Enter your username"
            required
          />
        </FormField>

        <FormField label="Password" required id="password">
          <Input
            id="password"
            type="password"
            bind:value={password}
            placeholder="Enter your password"
            required
          />
        </FormField>

        <Button variant="primary" fullWidth loading={$loading} disabled={$loading}>
          {isLogin ? 'Sign In' : 'Sign Up'}
        </Button>
      </form>

      <div class="mt-6 text-center">
        <Button variant="outline" on:click={toggleMode}>
          {isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in'}
        </Button>
      </div>
    </Card>
  </div>
</div>
