const path = require("path");
const webpack = require("webpack");
const childProcess = require("child_process");

const CopyPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");


const mode = process.env.mode;
const isDev = mode === "development";
const isProd = mode === "production";
const staticPath = path.resolve(__dirname, "../src/senaite/storage/browser/static");

console.log(`RUNNING WEBPACK IN '${mode}' MODE`);


module.exports = {
  // https://webpack.js.org/configuration/devtool
  devtool: isDev ? "eval" : "source-map",
  // https://webpack.js.org/configuration/mode/#usage
  mode: mode,
  context: path.resolve(__dirname, "app"),
  entry: {
    "senaite.storage": [
      "./senaite.storage.js",
      "./scss/senaite.storage.scss"
    ],
  },
  output: {
    filename: isDev ? "[name].js" : `[name].[contenthash].js`,
    path: path.resolve(staticPath, "bundles"),
    publicPath: "/++plone++senaite.storage.static/bundles"
  },
  module: {
    rules: [
      {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: ["babel-loader", "coffee-loader"]
      },
      {
        // JS
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/],
        use: [
          {
            // https://webpack.js.org/loaders/babel-loader/
            loader: "babel-loader"
          }
        ]
      },
      {
        // SCSS
        test: /\.s[ac]ss$/i,
        use: [
          {
            // https://webpack.js.org/plugins/mini-css-extract-plugin/
            loader: MiniCssExtractPlugin.loader,
          },
          {
            // https://webpack.js.org/loaders/css-loader/
            loader: "css-loader"
          },
          {
            // https://webpack.js.org/loaders/sass-loader/
            loader: "sass-loader"
          }
        ]
      },
      {
        test: /\.(png|jpg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            // https://webpack.js.org/loaders/file-loader/
            loader: "file-loader",
            options: {
              name: "[name].[ext]",
              outputPath: "../assets/img",
              publicPath: "/++plone++senaite.storage.static/assets/img",
            }
          }
        ]
      }
    ]
  },
  plugins: [
    // https://github.com/johnagan/clean-webpack-plugin
    new CleanWebpackPlugin({
      verbose: false,
      // Workaround in `watch` mode when trying to remove the `resources.pt` in the parent folder:
      // Error: clean-webpack-plugin: Cannot delete files/folders outside the current working directory.
      cleanAfterEveryBuildPatterns: ["!../*"],
    }),
    // https://webpack.js.org/plugins/html-webpack-plugin/
    new HtmlWebpackPlugin({
      inject: false,
      filename:  path.resolve(staticPath, "resources.pt"),
      template: "resources.pt",
    }),
    // https://webpack.js.org/plugins/mini-css-extract-plugin/
    new MiniCssExtractPlugin({
      filename: "[name].css"
    }),
    // https://webpack.js.org/plugins/copy-webpack-plugin/
    // new CopyPlugin({
    //   patterns: [
    //   ]
    // }),
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
    $: "jQuery",
    jquery: "jQuery",
    bootstrap: "bootstrap",
    tinyMCE: "tinymce"
  }
};
