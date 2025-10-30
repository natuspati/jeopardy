import { render, screen } from '@testing-library/react'; // Added screen
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import App from '@/App';

describe('App', () => {
  it('should display the Home link', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument();
  });

  it('should display the Game link', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByRole('link', { name: /game/i })).toBeInTheDocument();
  });
});
