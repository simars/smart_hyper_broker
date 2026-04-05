.PHONY: init dev dev-debug test clean

init:
	npm install

dev:
	npm run dev

dev-debug:
	NODE_OPTIONS='--inspect' npm run dev

test:
	npm run test --if-present

clean:
	rm -rf node_modules
	rm -rf .next
