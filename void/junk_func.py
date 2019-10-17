    def update_path_image(self):
        if self.step_count == 0: # init image
            self.path_im = Image.new('RGBA',self.parent.display.canvas_size,(0,0,0,0))
            self.path_draw = ImageDraw.Draw(self.path_im)
        else:
            if self.step_count % 2 == 0: fill="#0000FF"
            else: fill ="#00FF00"
            previous_point = self.previous_location
            current_point = self.location
            previous_point = (previous_point[1]*self.parent.display.canvas_size[0],previous_point[0]*self.parent.display.canvas_size[1])
            current_point = (current_point[1]*self.parent.display.canvas_size[0],current_point[0]*self.parent.display.canvas_size[1])
            self.path_draw.line((previous_point[0],previous_point[1],
                                 current_point[0],current_point[1]),
                                 fill=fill,width=2)
                                 