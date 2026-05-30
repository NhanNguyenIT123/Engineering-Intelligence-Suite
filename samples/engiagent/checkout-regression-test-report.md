# Checkout Regression Test Report

## Summary

During regression testing, the checkout service fails only on staging after the latest payment connector deployment.

## Environment

- Application: Web checkout
- Environment: staging
- Build: 2026.05.30-rc2
- Browser: Chrome 125
- Payment sandbox: PayBox test endpoint

## Expected

Payment confirmation is returned within 2 seconds after the user submits a valid card token.

## Actual

Staging returns HTTP 500 after 14 seconds when the sandbox provider is called.

## Reproduction Steps

1. Open staging checkout.
2. Add any product to cart.
3. Use test card token `tok_sandbox_success`.
4. Submit payment.
5. Observe timeout followed by HTTP 500.

## Notes

The failure is reproducible only on staging. Local development still returns success. The connector deployment changed the sandbox base URL and retry timeout settings.
