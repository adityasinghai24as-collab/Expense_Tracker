import { describe, it, expect, vi, beforeEach } from 'vitest';
import api, { expensesApi, categoriesApi } from './api';

vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  };
  return { default: mockAxios };
});

describe('API Services', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('expensesApi.getAll calls correct URL', async () => {
    api.get.mockResolvedValueOnce({ data: [] });
    await expensesApi.getAll(0, 10);
    expect(api.get).toHaveBeenCalledWith('/expenses?skip=0&limit=10');
  });

  it('expensesApi.getAll with category calls correct URL', async () => {
    api.get.mockResolvedValueOnce({ data: [] });
    await expensesApi.getAll(0, 10, 5);
    expect(api.get).toHaveBeenCalledWith('/expenses?skip=0&limit=10&category_id=5');
  });

  it('categoriesApi.create calls correct URL', async () => {
    const newCat = { name: 'Food' };
    api.post.mockResolvedValueOnce({ data: newCat });
    await categoriesApi.create(newCat);
    expect(api.post).toHaveBeenCalledWith('/categories', newCat);
  });
});
