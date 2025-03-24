const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');

const mode = process.argv.indexOf("production") !== -1 ? "production" : "development";
console.log(`Webpack mode: ${mode}`);

let plugins = [
  new BundleTracker({ path: __dirname, filename: 'webpack-stats.json' }),
  new MiniCssExtractPlugin({
    filename: 'css/[name].[contenthash].css',
  }),
  new webpack.ProvidePlugin({
    $: 'jquery',
    jQuery: 'jquery',
    'window.jQuery': 'jquery',
  }),
  new webpack.ProvidePlugin({
    Leaflet: 'leaflet',
  }),
];

if (mode === 'development') {
  // Only add LiveReloadPlugin in development mode
  const LiveReloadPlugin = require('webpack-livereload-plugin');
  plugins.push(new LiveReloadPlugin({ appendScriptTag: true }));
}

module.exports = {
  entry: './base/static/js/index',
  output: {
    path: path.resolve('./base/static/bundles'),
    filename: "[name].[contenthash].js",
  },
  plugins: plugins,
  module: {
    rules: [
      // Expose jQuery globally
      {
        test: require.resolve('jquery'),
        loader: 'expose-loader',
        options: {
          exposes: ['$', 'jQuery'],
        },
      },
      // Expose DataTables globally
      {
        test: require.resolve('datatables.net'),
        loader: 'expose-loader',
        options: {
          exposes: ['DataTable'],
        },
      },
      // Expose Moment.js globally
      {
        test: require.resolve('moment'),
        loader: 'expose-loader',
        options: {
          exposes: ['moment'],
        },
      },
      // Expose Leaflet globally
      {
        test: require.resolve('leaflet'),
        loader: 'expose-loader',
        options: {
          exposes: ['Leaflet'],
        },
      },
      // Expose AirDatepicker globally
      {
        test: require.resolve('air-datepicker'),
        loader: 'expose-loader',
        options: {
          exposes: ['AirDatepicker'],
        },
      },
      // Expose localeEn globally
      {
        test: require.resolve('air-datepicker/locale/en'),
        loader: 'expose-loader',
        options: {
          exposes: ['localeEn'],
        },
      },
      // CSS and SCSS rules
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
            },
          },
        ],
      },
    ],
  },
  stats: {
    assets: false,           // Hide assets info
    chunks: false,           // Hide chunks info
    modules: false,          // Hide modules info
    entrypoints: false,      // Hide entrypoints info
    performance: false,      // Hide performance info
    errors: true,            // Show only errors
    errorDetails: true,      // Include detailed error messages
    warnings: true,          // Show warnings
    builtAt: true,           // Show when the build was created
    colors: true,            // Colorized output
  },
};