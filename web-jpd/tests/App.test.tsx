import { render, screen } from '@testing-library/react'; // Added screen
import userEvent from '@testing-library/user-event'; // Added userEvent
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

  it('should increment the count when the button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    const countButton = screen.getByRole('button', { name: /count is 0/i });
    expect(countButton).toBeInTheDocument();
    expect(countButton).toHaveTextContent('count is 0');

    await user.click(countButton);
    expect(countButton).toHaveTextContent('count is 1');

    await user.click(countButton);
    expect(countButton).toHaveTextContent('count is 2');
  });
});
